import pytest
import json

from aws_cdk import App
from aws_cdk import Environment

from aws_cdk.assertions import Template


ENVIRONMENT = Environment(
    account='testing',
    region='testing'
)


def test_waf_match_with_snapshot(snapshot):
    from waf.acl import WAF
    from waf.acl import WAFProps
    from waf.rules import get_rules
    app = App()
    abc_waf = WAF(
        app,
        'abc',
        props=WAFProps(
            rules=get_rules('abc'),
            prefix='abc',
            ips_to_allow=[
                '98.35.33.121/32',
            ],
            ips_to_block=[
                '192.0.2.0/24',
                '184.1.0.0/16',
            ]
        ),
    )
    template = Template.from_stack(
        abc_waf,
    )
    snapshot.assert_match(
        json.dumps(
            template.to_json(),
            indent=4,
            sort_keys=True
        ),
        'abc_waf.json'
    )
