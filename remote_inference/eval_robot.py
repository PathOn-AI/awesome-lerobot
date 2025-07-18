#!/usr/bin/env python

import time
import logging
import asyncio
import argparse

import torch
import cv2
import numpy as np
import os

# No need to import policies - handled by remote server
from lerobot.common.robot_devices.utils import busy_wait
from lerobot.common.robot_devices.robots.utils import make_robot
from lerobot_client import LeRobotClient
from datetime import datetime
import os
import shutil


async def run_inference(task: str = None, 
                       inference_time_s: int = 30, fps: int = 25, device: str = "mps",
                       robot_type: str = "so100", output_dir: str = "images/",
                       websocket_url: str = "ws://localhost:8765"):
    """Main async inference function."""
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Initialize robot (policy is handled by remote WebSocket server)
    robot = make_robot(robot_type)
    robot.connect()

    # Setup output directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Performance tracking variables
    iteration_times = []
    running_total_time = 0.0
    successful_steps = 0
    start_overall = time.perf_counter()

    # Use async context manager for LeRobotClient
    async with LeRobotClient(websocket_url) as client:
        logging.info("✅ LeRobot client connected and ready")
        
        try:
            # Main inference loop
            for step in range(inference_time_s * fps):
                print('Iteration Start Time:', datetime.now().strftime("%A, %B %d, %Y at %H:%M:%S.%f")[:-3])
                start_time = time.perf_counter()
                observation = robot.capture_observation()
                
                # Save images
                image = observation['observation.images.phone']
                np_image = np.array(image)
                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(os.path.join(output_dir, f"image_phone_{step}.jpg"), np_image)
                
                image = observation['observation.images.on_robot']
                np_image = np.array(image)
                np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(os.path.join(output_dir, f"image_on_robot_{step}.jpg"), np_image)
                
                print(f"Step {step}")
                
                # Process observation
                for name in observation:
                    observation[name] = observation[name].numpy()
                    print(name, observation[name].shape)

                # Add task if specified (needed for PI0 and SmolVLA models)
                if task:
                    observation["task"] = [task]
                    
                print('Done processing observation:', datetime.now().strftime("%A, %B %d, %Y at %H:%M:%S.%f")[:-3])
                
                try:
                    # Get action directly from client
                    action = await client.select_action(observation)
                    print('Get Action Time:', datetime.now().strftime("%A, %B %d, %Y at %H:%M:%S.%f")[:-3])
                    action = torch.from_numpy(action)
                    action = action.squeeze(0)
                    print('Action Conversion Time:', datetime.now().strftime("%A, %B %d, %Y at %H:%M:%S.%f")[:-3])
                    robot.send_action(action)
                    print('Robot Send Action Time:', datetime.now().strftime("%A, %B %d, %Y at %H:%M:%S.%f")[:-3])
                    
                    # Calculate iteration performance
                    iteration_time = time.perf_counter() - start_time
                    iteration_ms = iteration_time * 1000
                    
                    # Update running averages
                    successful_steps += 1
                    running_total_time += iteration_time
                    iteration_times.append(iteration_time)
                    
                    # Calculate running averages
                    running_avg_ms = (running_total_time / successful_steps) * 1000
                    running_avg_fps = 1.0 / (running_total_time / successful_steps)
                    
                    # Calculate overall performance since start
                    elapsed_overall = time.perf_counter() - start_overall
                    overall_fps = successful_steps / elapsed_overall
                    
                    # Print performance stats
                    print(f"📊 Step {step}: {iteration_ms:.1f}ms | "
                          f"Avg: {running_avg_ms:.1f}ms ({running_avg_fps:.1f} FPS) | "
                          f"Overall: {overall_fps:.1f} FPS | "
                          f"Success: {successful_steps}/{step+1}")
                    
                except Exception as e:
                    logging.error(f"Failed to get action at step {step}: {e}")
                    # Print failure stats
                    elapsed_overall = time.perf_counter() - start_overall
                    overall_fps = successful_steps / elapsed_overall if successful_steps > 0 else 0
                    print(f"❌ Step {step}: FAILED | "
                          f"Overall: {overall_fps:.1f} FPS | "
                          f"Success: {successful_steps}/{step+1}")
                    continue

                dt_s = time.perf_counter() - start_time
                busy_wait(1 / fps - dt_s)

        finally:
            # Print final performance summary
            total_elapsed = time.perf_counter() - start_overall
            
            print("\n" + "="*60)
            print("📈 FINAL PERFORMANCE SUMMARY")
            print("="*60)
            
            if successful_steps > 0:
                final_avg_ms = (running_total_time / successful_steps) * 1000
                final_avg_fps = 1.0 / (running_total_time / successful_steps)
                overall_fps = successful_steps / total_elapsed
                success_rate = (successful_steps / (inference_time_s * fps)) * 100
                
                print(f"Total steps attempted: {inference_time_s * fps}")
                print(f"Successful steps: {successful_steps}")
                print(f"Success rate: {success_rate:.1f}%")
                print(f"Average iteration time: {final_avg_ms:.1f}ms")
                print(f"Average processing FPS: {final_avg_fps:.1f}")
                print(f"Overall throughput FPS: {overall_fps:.1f}")
                print(f"Total runtime: {total_elapsed:.1f}s")
                
                # Additional stats if you want them
                if len(iteration_times) > 1:
                    import statistics
                    median_ms = statistics.median(iteration_times) * 1000
                    print(f"Median iteration time: {median_ms:.1f}ms")
            else:
                print("❌ No successful iterations completed")
            
            print("="*60)
            
            # Robot cleanup (client cleanup handled by context manager)
            try:
                robot.disconnect()
                logging.info("✅ Robot disconnected")
            except Exception as e:
                logging.warning(f"Error during robot cleanup: {e}")


def main():
    """Entry point that runs the async inference."""
    parser = argparse.ArgumentParser(description="Run robot evaluation with remote WebSocket server")
    parser.add_argument("--task", 
                       help="Task description (required for certain models like PI0 and SmolVLA)")
    parser.add_argument("--inference-time", type=int, default=30,
                       help="Inference time in seconds (default: 30)")
    parser.add_argument("--fps", type=int, default=25,
                       help="Frames per second (default: 25)")
    parser.add_argument("--device", default="mps",
                       help="Device to use (default: mps)")
    parser.add_argument("--robot-type", default="so100",
                       help="Robot type (default: so100)")
    parser.add_argument("--output-dir", default="images/",
                       help="Output directory for images (default: images/)")
    parser.add_argument("--websocket-url", default="ws://localhost:8765",
                       help="WebSocket server URL (default: ws://localhost:8765)")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(run_inference(
            task=args.task,
            inference_time_s=args.inference_time,
            fps=args.fps,
            device=args.device,
            robot_type=args.robot_type,
            output_dir=args.output_dir,
            websocket_url=args.websocket_url
        ))
    except KeyboardInterrupt:
        logging.info("Inference interrupted by user")
    except Exception as e:
        logging.error(f"Inference failed: {e}")
        raise


if __name__ == "__main__":
    main()