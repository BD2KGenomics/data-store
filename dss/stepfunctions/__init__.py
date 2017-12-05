import json
import os
import typing

import boto3


def step_functions_invoke(state_machine_name_template: str, execution_name: str, input) -> typing.Any:
    """
    Invoke a step functions state machine.  The name of the state machine to be invoked will be derived from
    `state_machine_name_template`, with string formatting to replace {stage} with the dss deployment stage.
    :param state_machine_name_template:
    :param execution_name:
    :param input:
    :return:
    """

    sfn = boto3.client('stepfunctions')
    sts_client = boto3.client("sts")

    execution_input = json.dumps(input)

    region = boto3.Session().region_name
    accountid = sts_client.get_caller_identity()['Account']
    stage = os.environ["DSS_DEPLOYMENT_STAGE"]
    sfn_name = state_machine_name_template.format(stage=stage)
    state_machine_arn = f"arn:aws:states:{region}:{accountid}:stateMachine:{sfn_name}"
    response = sfn.start_execution(
        stateMachineArn=state_machine_arn,
        name=execution_name,
        input=execution_input
    )
    return response