# MIT License

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


from pydantic import root_validator
from typing import Any, Dict, List, Optional

from action_msgs.msg import GoalStatus
from llama_msgs.msg import LogitBias
from llama_msgs.action import GenerateResponse
from llama_msgs.srv import Tokenize
from llama_ros.llama_client_node import LlamaClientNode

from langchain_core.language_models.llms import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun


class LlamaROS(LLM):

    namespace: str = "llama"
    llama_client: LlamaClientNode = None

    # sampling params
    n_prev: int = 64
    n_probs: int = 1

    ignore_eos: bool = False
    logit_bias: Dict[int, float] = {}

    temp: float = 0.80
    dynatemp_range: float = 0.0
    dynatemp_exponent: float = 1.0

    top_k: int = 40
    top_p: float = 0.95
    min_p: float = 0.05
    tfs_z: float = 1.00
    typical_p: float = 1.00

    penalty_last_n: int = 64
    penalty_repeat: float = 1.10
    penalty_freq: float = 0.00
    penalty_present: float = 0.00

    mirostat: int = 0
    mirostat_eta: float = 0.10
    mirostat_tau: float = 5.0

    penalize_nl: bool = True

    samplers_sequence: str = "kfypmt"

    grammar: str = ""
    grammar_schema: str = ""

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        values["llama_client"] = LlamaClientNode.get_instance(
            values["namespace"])
        return values

    @property
    def _default_params(self) -> Dict[str, Any]:
        return {}

    @property
    def _llm_type(self) -> str:
        return "llamaros"

    def cancel(self) -> None:
        self.llama_client.cancel_generate_text()

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:

        goal = GenerateResponse.Goal()
        goal.prompt = prompt
        goal.reset = True

        # sampling params
        goal.sampling_config.n_prev = self.n_prev
        goal.sampling_config.n_probs = self.n_probs

        goal.sampling_config.ignore_eos = self.ignore_eos
        for key in self.logit_bias:
            lb = LogitBias()
            lb.token = key
            lb.bias = self.logit_bias[key]
            goal.sampling_config.logit_bias.data.append(lb)

        goal.sampling_config.temp = self.temp
        goal.sampling_config.dynatemp_range = self.dynatemp_range
        goal.sampling_config.dynatemp_exponent = self.dynatemp_exponent

        goal.sampling_config.top_k = self.top_k
        goal.sampling_config.top_p = self.top_p
        goal.sampling_config.min_p = self.min_p
        goal.sampling_config.tfs_z = self.tfs_z
        goal.sampling_config.typical_p = self.typical_p

        goal.sampling_config.penalty_last_n = self.penalty_last_n
        goal.sampling_config.penalty_repeat = self.penalty_repeat
        goal.sampling_config.penalty_freq = self.penalty_freq
        goal.sampling_config.penalty_present = self.penalty_present

        goal.sampling_config.mirostat = self.mirostat
        goal.sampling_config.mirostat_eta = self.mirostat_eta
        goal.sampling_config.mirostat_tau = self.mirostat_tau

        goal.sampling_config.penalize_nl = self.penalize_nl

        goal.sampling_config.samplers_sequence = self.samplers_sequence

        goal.sampling_config.grammar = self.grammar
        goal.sampling_config.grammar_schema = self.grammar_schema

        # send goal
        result, status = LlamaClientNode.get_instance(
            self.namespace).generate_response(goal)

        if status != GoalStatus.STATUS_SUCCEEDED:
            return ""
        return result.response.text

    def get_num_tokens(self, text: str) -> int:
        req = Tokenize.Request()
        req.prompt = text
        tokens = self.llama_client.tokenize(req).tokens
        return len(tokens)
