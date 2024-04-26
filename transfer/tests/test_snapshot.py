import pytest
import json

from aws_cdk import App
from aws_cdk import Environment

from aws_cdk.assertions import Template


ENVIRONMENT = Environment(
    account='testing',
    region='testing'
)


def test_anvil_file_transfer_matches_snapshot(snapshot):
    from transfer.anvil import AnvilFileTransferStack
    app = App()
    aft = AnvilFileTransferStack(
        app,
        'AnvilFileTransferStack',
        env=ENVIRONMENT,
    )
    template = Template.from_stack(
        aft
    )
    snapshot.assert_match(
        json.dumps(
            template.to_json(),
            indent=4,
            sort_keys=True
        ),
        'anvil_file_transfer_stack.json'
    )
