"""
OpenAI Gym Environment for Procurement Optimization
Uses Reinforcement Learning to learn optimal purchasing strategies
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class ProcurementEnvironment(gym.Env):
    """
    Custom Gym Environment for procurement decision-making

    State Space:
        - current_price: float (normalized)
        - price_trend: float (-1 to 1, down/stable/up)
        - inventory_level: int (0-100)
        - days_until_deadline: int (0-30)
        - supplier_rating: float (0-5)
        - delivery_time: int (1-14)

    Action Space:
        - 0: Buy now
        - 1: Wait 1 day
        - 2: Wait 3 days
        - 3: Wait 1 week
        - 4: Buy in bulk (2x quantity)

    Reward Structure:
        - Positive reward for buying at lower price
        - Negative reward for missing deadline
        - Bonus for buying from high-rated suppliers
    """

    def __init__(self, config: Dict = None):
        super().__init__()

        self.config = config or {}

        # Define action space: 5 possible actions
        self.action_space = spaces.Discrete(5)

        # Define observation space: 6 features
        self.observation_space = spaces.Box(
            low=np.array([0, -1, 0, 0, 0, 1], dtype=np.float32),
            high=np.array([1, 1, 100, 30, 5, 14], dtype=np.float32),
            dtype=np.float32
        )

        # Initialize state
        self.reset()

    def reset(self, seed=None, options=None):
        """Reset environment to initial state"""
        super().reset(seed=seed)

        self.current_price = random.uniform(80, 120)  # Normalized price (80-120% of baseline)
        self.price_trend = random.uniform(-0.05, 0.05)  # Daily price change
        self.inventory = random.randint(20, 60)  # Current inventory level
        self.days_left = random.randint(7, 30)  # Days until deadline
        self.supplier_rating = random.uniform(3, 5)  # Supplier rating
        self.delivery_time = random.randint(1, 7)  # Delivery days

        return self._get_obs(), {}

    def _get_obs(self):
        """Get current observation"""
        return np.array([
            self.current_price / 150,  # Normalize price
            self.price_trend * 20,  # Scale trend
            self.inventory,
            self.days_left,
            self.supplier_rating,
            self.delivery_time
        ], dtype=np.float32)

    def step(self, action):
        """Execute action and return new state, reward, done"""

        reward = 0
        price_change = 0

        # Execute action
        if action == 0:  # Buy now
            cost = self.current_price * 100  # Base cost
            reward += 100 - cost  # Reward for good price
            reward += self.supplier_rating * 5  # Bonus for good supplier
            self.inventory += 100

        elif action == 1:  # Wait 1 day
            price_change = self.price_trend
            reward -= 0.5  # Small waiting penalty

        elif action == 2:  # Wait 3 days
            price_change = self.price_trend * 3
            reward -= 1  # Medium waiting penalty

        elif action == 3:  # Wait 1 week
            price_change = self.price_trend * 7
            reward -= 2  # Larger waiting penalty

        elif action == 4:  # Buy in bulk
            cost = self.current_price * 300  # Bulk purchase
            reward += 300 - cost * 0.95  # Bulk discount
            reward += self.supplier_rating * 8  # Bulk bonus
            self.inventory += 300

        # Update price based on trend
        self.current_price += price_change
        self.current_price = max(60, min(140, self.current_price))  # Keep in range

        # Update days left
        if action in [1, 2, 3]:
            days_passed = [1, 3, 7][[1, 2, 3].index(action)] if action in [1, 2, 3] else 0
            self.days_left -= days_passed

        # Reward for having enough inventory
        if self.inventory >= 500:
            reward += 50  # Target inventory reached
        elif self.inventory >= 300:
            reward += 20
        elif self.inventory >= 100:
            reward += 5

        # Penalty for missing deadline
        if self.days_left <= 0 and self.inventory < 500:
            reward -= 100  # Large penalty for failure
            return self._get_obs(), reward, True, False, {}

        # Check if episode is done
        done = self.inventory >= 500 or self.days_left <= 0

        return self._get_obs(), reward, done, False, {}

    def render(self, mode='human'):
        """Render environment state"""
        print(f"Price: ${self.current_price:.2f} | Trend: {self.price_trend:.3f}")
        print(f"Inventory: {self.inventory} | Days Left: {self.days_left}")
        print(f"Supplier Rating: {self.supplier_rating:.1f} | Delivery: {self.delivery_time} days")
        print("-" * 50)


class ProcurementAgent:
    """
    Reinforcement Learning Agent for Procurement Decisions
    Uses Q-Learning to learn optimal purchasing strategy
    """

    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=1.0):
        self.q_table = {}  # Q-values for state-action pairs
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01

    def get_action(self, state, env):
        """Choose action using epsilon-greedy policy"""
        state_tuple = tuple(state)

        if random.random() < self.epsilon:
            return env.action_space.sample()  # Explore
        else:
            # Exploit: choose best known action
            if state_tuple in self.q_table:
                return np.argmax(self.q_table[state_tuple])
            else:
                return env.action_space.sample()

    def update(self, state, action, reward, next_state, done):
        """Update Q-values using Q-learning update rule"""
        state_tuple = tuple(state)
        next_state_tuple = tuple(next_state)

        # Initialize Q-values if not present
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(5)
        if next_state_tuple not in self.q_table:
            self.q_table[next_state_tuple] = np.zeros(5)

        # Q-learning update
        best_next_q = np.max(self.q_table[next_state_tuple]) if not done else 0
        td_target = reward + self.gamma * best_next_q
        td_error = td_target - self.q_table[state_tuple][action]
        self.q_table[state_tuple][action] += self.lr * td_error

        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def train(self, env, episodes=1000):
        """Train the agent"""
        rewards_history = []

        for episode in range(episodes):
            state, _ = env.reset()
            total_reward = 0
            done = False

            while not done:
                action = self.get_action(state, env)
                next_state, reward, done, _, _ = env.step(action)
                self.update(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward

            rewards_history.append(total_reward)

            if (episode + 1) % 100 == 0:
                avg_reward = np.mean(rewards_history[-100:])
                logger.info(f"Episode {episode + 1}: Avg Reward = {avg_reward:.2f}, Epsilon = {self.epsilon:.3f}")

        return rewards_history

    def get_best_strategy(self, env, current_state):
        """Get optimal action for current state"""
        action = self.get_action(current_state, env)
        actions = ["Buy Now", "Wait 1 Day", "Wait 3 Days", "Wait 1 Week", "Buy Bulk"]
        return actions[action]


# Singleton instance
procurement_agent = ProcurementAgent()