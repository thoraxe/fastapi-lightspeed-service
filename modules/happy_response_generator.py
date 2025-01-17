import logging, sys
from string import Template
from modules.model_context import get_watsonx_predictor
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from string import Template

DEFAULT_MODEL = "ibm/granite-13b-chat-v1"


class HappyResponseGenerator:
    def __init__(self):
        logging.basicConfig(
            stream=sys.stdout,
            format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            level=logging.INFO,
        )
        self.logger = logging.getLogger("happy_response_generator")

    def generate(self, conversation, string, **kwargs):
        if "model" in kwargs:
            model = kwargs["model"]
        else:
            model = DEFAULT_MODEL

        if "verbose" in kwargs:
            if kwargs["verbose"] == "True" or kwargs["verbose"] == "true":
                verbose = True
            else:
                verbose = False
        else:
            verbose = False

        # TODO: must be a smarter way to do this
        settings_string = Template(
            '{"conversation": "$conversation", "query": "$query","model": "$model", "verbose": "$verbose"}'
        )

        self.logger.info(
            conversation
            + " call settings: "
            + settings_string.substitute(
                conversation=conversation, query=string, model=model, verbose=verbose
            )
        )

        prompt_instructions = PromptTemplate.from_template(
            """Instructions:
- you are a helpful assistant
- your job is to generate a pleasant response to a question
- you should try to paraphrase the question that was asked in your response
- here are several examples

Examples:
Question: How do I configure autoscaling for my cluster?
Response: I'd be happy to help you with configuring autoscaling for your cluster.

Question: ensure that all volumes created in the namespace backend-recommendations-staging are at least 2 gigabytes in size
Response: OK, I help you with ensuring the volumes are at least 2 gigabytes in size.

Question: give me 5 pod nginx deployment with the 200mi memory limit
Response: I can definitely help create a deployment for that.

Question: {question}
Response:
"""
        )

        self.logger.info(conversation + " usng model: " + model)
        self.logger.info(conversation + " user query: " + string)
        query = prompt_instructions.format(question=string)

        self.logger.info(conversation + " full prompt: " + query)

        bare_llm = get_watsonx_predictor(model=model, temperature=2)
        llm_chain = LLMChain(llm=bare_llm, prompt=prompt_instructions, verbose=verbose)

        response = llm_chain(inputs={"question": string})

        self.logger.info(conversation + " happy response: " + str(response))

        return str(response)


if __name__ == "__main__":
    """to execute, from the repo root, use python -m modules.happy_response_generator"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate a pleasant prefix for the response to the user")
    parser.add_argument(
        "-c",
        "--conversation-id",
        default="1234",
        type=str,
        help="A short identifier for the conversation",
    )
    parser.add_argument(
        "-q",
        "--query",
        default="create a quota to cap the total memory requests to 128 gigabytes in the namespace sunless-sunshine",
        type=str,
        help="The user prompt",
    )
    parser.add_argument(
        "-m", "--model", default=DEFAULT_MODEL, type=str, help="The model to use"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=False,
        help="Set Verbose status of langchains [True/False]",
    )

    args = parser.parse_args()

    happy_response_generator = HappyResponseGenerator()
    happy_response_generator.generate(
        args.conversation_id, args.query, model=args.model, verbose=args.verbose
    )

