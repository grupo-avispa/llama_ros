#!/usr/bin/env python3

# MIT License

# Copyright (c) 2024  Alejandro González Cantón
# Copyright (c) 2024  Miguel Ángel González Santamarta

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import time
from random import randint

import rclpy
from rclpy.node import Node

from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from llama_ros.langchain import ChatLlamaROS


@tool
def get_inhabitants(city: str) -> int:
    """Get the current temperature of a city"""
    return randint(4_000_000, 8_000_000)


@tool
def get_curr_temperature(city: str) -> int:
    """Get the current temperature of a city"""
    return randint(20, 30)


class ChatLlamaLanggraphDemoNode(Node):

    def __init__(self) -> None:
        super().__init__("chatllama_langgraph_demo_node")

        self.chat = ChatLlamaROS(temp=0.0, template_method="jinja")
        self.agent_executor = create_react_agent(
            self.chat, [get_inhabitants, get_curr_temperature]
        )

    def send_prompt(self) -> None:

        initial_time = time.time()

        response = self.agent_executor.invoke(
            {
                "messages": [
                    HumanMessage(
                        content="What is the current temperature in Madrid? And its inhabitants?"
                    )
                ]
            }
        )

        end_time = time.time()

        self.get_logger().info(f"\nResponse: {response['messages'][-1].content}")
        self.get_logger().info(f"Time to run the agent: {end_time - initial_time} s")


def main():
    rclpy.init()
    node = ChatLlamaLanggraphDemoNode()
    node.send_prompt()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
