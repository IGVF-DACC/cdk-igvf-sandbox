from typing import List, Dict, Any


def add_prefix_to_visibility_config_metric_config(rule: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    if rule.get('VisibilityConfig', {}).get('MetricName') is not None:
        rule['VisibilityConfig']['MetricName'] = f"{prefix}-{rule['VisibilityConfig']['MetricName']}"
    return rule


def reset_priority(rule: Dict[str, Any], idx: int) -> Dict[str, Any]:
    rule['Priority'] = idx * 100
    return rule


def get_rules(prefix: str) -> List[Dict[str, Any]]:
    rules = [
        {
            "Name": "throttle-requests",
            "Priority": 100,
            "Statement": {
                "RateBasedStatement": {
                    "Limit": 600,
                    "EvaluationWindowSec": 300,
                    "AggregateKeyType": "IP"
                }
            },
            "Action": {
                "Block": {
                    "CustomResponse": {
                        "ResponseCode": 429,
                        "CustomResponseBodyKey": "RateLimitBody"
                    }
                }
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "waf-throttle-requests"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesAmazonIpReputationList",
            "Priority": 101,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesAmazonIpReputationList"
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesAmazonIpReputationList"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesAnonymousIpList",
            "Priority": 102,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesAnonymousIpList"
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesAnonymousIpList"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesLinuxRuleSet",
            "Priority": 103,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesLinuxRuleSet"
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesLinuxRuleSet"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesPHPRuleSet",
            "Priority": 104,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesPHPRuleSet"
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesPHPRuleSet"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesUnixRuleSet",
            "Priority": 105,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesUnixRuleSet"
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesUnixRuleSet"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesCommonRuleSet",
            "Priority": 200,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesCommonRuleSet",
                    "RuleActionOverrides": [
                        {
                            "Name": "SizeRestrictions_BODY",
                            "ActionToUse": {
                                "Count": {}
                            }
                        },
                        {
                            "Name": "SizeRestrictions_URIPATH",
                            "ActionToUse": {
                                "Count": {}
                            }
                        }
                    ]
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesCommonRuleSet"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesKnownBadInputsRuleSet",
            "Priority": 300,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesKnownBadInputsRuleSet"
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesKnownBadInputsRuleSet"
            }
        },
        {
            "Name": "AWS-AWSManagedRulesBotControlRuleSet",
            "Priority": 400,
            "Statement": {
                "ManagedRuleGroupStatement": {
                    "VendorName": "AWS",
                    "Name": "AWSManagedRulesBotControlRuleSet",
                    "ManagedRuleGroupConfigs": [
                        {
                            "AWSManagedRulesBotControlRuleSet": {
                                "InspectionLevel": "COMMON"
                            }
                        }
                    ]
                }
            },
            "OverrideAction": {
                "None": {}
            },
            "VisibilityConfig": {
                "SampledRequestsEnabled": True,
                "CloudWatchMetricsEnabled": True,
                "MetricName": "AWS-AWSManagedRulesBotControlRuleSet"
            }
        }
    ]
    return [
        reset_priority(
            add_prefix_to_visibility_config_metric_config(
                rule,
                prefix
            ),
            idx + 1
        )
        for idx, rule in enumerate(rules)
    ]
