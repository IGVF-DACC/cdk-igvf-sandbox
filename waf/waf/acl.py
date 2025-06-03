from aws_cdk import CfnOutput
from aws_cdk import Stack
from aws_cdk import RemovalPolicy
from aws_cdk import Tags

from constructs import Construct

from aws_cdk.aws_wafv2 import CfnWebACL
from aws_cdk.aws_wafv2 import CfnIPSet

from typing import Any, List, Dict, Optional

from dataclasses import dataclass


CUSTOM_RESPONSE_RATE_LIMIT = '{"error": "Too many requests", "message": "You have exceeded request limit. Try again later."}'


@dataclass
class WAFProps:
    rules: List[Dict[str, Any]]
    prefix: str
    ips_to_block: Optional[List[str]] = None
    ips_to_allow: Optional[List[str]] = None


class WAF(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            *,
            props: WAFProps,
            **kwargs: Any
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.cfn_web_acl = CfnWebACL(
            self,
            ''.join([part.title() for part in props.prefix.split('-')]),
            default_action={
                'allow': {}
            },
            scope='REGIONAL',
            visibility_config={
                'cloudWatchMetricsEnabled': True,
                'sampledRequestsEnabled': True,
                'metricName': f'{props.prefix}Metrics',
            },
            custom_response_bodies={
                'RateLimitBody': {
                    'contentType': 'APPLICATION_JSON',
                    'content': CUSTOM_RESPONSE_RATE_LIMIT
                }
            }
        )

        self.cfn_web_acl.add_property_override(
            'Rules',
            props.rules,
        )

        if props.ips_to_block:
            self.blocked_ips = CfnIPSet(
                self,
                f'{props.prefix}-blocked-ips',
                addresses=props.ips_to_block,
                ip_address_version='IPV4',
                scope='REGIONAL',
                description='Blocked IPs',
            )
            block_rule = [
                {
                    'Name': 'block-ips',
                    'Priority': 50,
                    'Statement': {
                        'IPSetReferenceStatement': {
                            'Arn': self.blocked_ips.attr_arn
                        }
                    },
                    'Action': {
                        'Block': {}
                    },
                    'VisibilityConfig': {
                        'SampledRequestsEnabled': True,
                        'CloudWatchMetricsEnabled': True,
                        'MetricName': f'{props.prefix}-blocked-ips'
                    }
                }
            ]
            props.rules = block_rule + props.rules

        if props.ips_to_allow:
            self.allowed_ips = CfnIPSet(
                self,
                f'{props.prefix}-allowed-ips',
                addresses=props.ips_to_allow,
                ip_address_version='IPV4',
                scope='REGIONAL',
                description='Allowed IPs',
            )
            allow_rule = [
                {
                    'Name': 'allow-ips',
                    'Priority': 40,
                    'Statement': {
                        'IPSetReferenceStatement': {
                            'Arn': self.allowed_ips.attr_arn
                        }
                    },
                    'Action': {
                        'Allow': {}
                    },
                    'VisibilityConfig': {
                        'SampledRequestsEnabled': True,
                        'CloudWatchMetricsEnabled': True,
                        'MetricName': f'{props.prefix}-allowed-ips'
                    }
                }
            ]
            props.rules = allow_rule + props.rules

        self.cfn_web_acl.add_property_override(
            'Rules',
            props.rules,
        )
