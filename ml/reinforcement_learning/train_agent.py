"""
Train the Reinforcement Learning Agent for Procurement Optimization
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ml.reinforcement_learning.procurement_env import ProcurementEnvironment, ProcurementAgent
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_procurement_agent():
    """Train the RL agent"""
    logger.info("=" * 60)
    logger.info("Training Procurement Optimization Agent")
    logger.info("=" * 60)

    # Create environment and agent
    env = ProcurementEnvironment()
    agent = ProcurementAgent()

    # Train agent
    logger.info("\nStarting training...")
    rewards = agent.train(env, episodes=2000)

    # Plot training progress
    plt.figure(figsize=(10, 6))
    plt.plot(rewards)
    plt.title('Procurement Agent Training Progress')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.grid(True, alpha=0.3)
    plt.savefig('ml/reinforcement_learning/training_progress.png')
    plt.show()

    logger.info("\n" + "=" * 60)
    logger.info("✅ Training Complete!")
    logger.info(f"Final Epsilon: {agent.epsilon:.4f}")
    logger.info(f"Q-Table Size: {len(agent.q_table)}")
    logger.info(f"Training chart saved to: ml/reinforcement_learning/training_progress.png")

    # Test trained agent
    logger.info("\n" + "=" * 60)
    logger.info("Testing Trained Agent")
    logger.info("=" * 60)

    state, _ = env.reset()
    total_reward = 0
    step = 0

    while True:
        action = agent.get_action(state, env)
        action_names = ["Buy Now", "Wait 1 Day", "Wait 3 Days", "Wait 1 Week", "Buy Bulk"]

        logger.info(f"\nStep {step + 1}:")
        logger.info(f"  Price: ${env.current_price:.2f}")
        logger.info(f"  Inventory: {env.inventory}")
        logger.info(f"  Days Left: {env.days_left}")
        logger.info(f"  Action: {action_names[action]}")

        next_state, reward, done, _, _ = env.step(action)
        total_reward += reward
        state = next_state
        step += 1

        if done:
            logger.info(f"\n🎯 Goal Achieved!")
            logger.info(f"  Final Inventory: {env.inventory}")
            logger.info(f"  Days Used: {step}")
            logger.info(f"  Total Reward: {total_reward:.2f}")
            break

    return agent


if __name__ == "__main__":
    agent = train_procurement_agent()