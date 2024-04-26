from aws_cdk import Stack
from aws_cdk import Size

from aws_cdk.aws_ec2 import SubnetSelection
from aws_cdk.aws_ec2 import SubnetType

from aws_cdk.aws_ecs import AwsLogDriverMode
from aws_cdk.aws_ecs import LogDriver
from aws_cdk.aws_ecs import ContainerImage

from aws_cdk.aws_secretsmanager import Secret as SMSecret

from aws_cdk.aws_ecr_assets import Platform

from aws_cdk.aws_iam import Role
from aws_cdk.aws_iam import ServicePrincipal

from aws_cdk.aws_batch import FargateComputeEnvironment
from aws_cdk.aws_batch import JobQueue
from aws_cdk.aws_batch import EcsFargateContainerDefinition
from aws_cdk.aws_batch import EcsJobDefinition
from aws_cdk.aws_batch import Secret

from aws_cdk.aws_events import Rule
from aws_cdk.aws_events import Schedule
from aws_cdk.aws_events import EventPattern
from aws_cdk.aws_events import EventField
from aws_cdk.aws_events import Connection
from aws_cdk.aws_events import ApiDestination
from aws_cdk.aws_events import RuleTargetInput

from aws_cdk.aws_events_targets import BatchJob
from aws_cdk.aws_events_targets import ApiDestination as TargetApiDestination

from aws_cdk.aws_ssm import StringParameter

from aws_cdk.aws_logs import RetentionDays

from aws_cdk.aws_ec2 import Vpc

from constructs import Construct


class AnvilFileTransferStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = Vpc.from_lookup(
            self,
            'Vpc',
            vpc_id='vpc-0048042cde3da83e3'
        )

        compute_environment = FargateComputeEnvironment(
            self,
            'ComputeEnvironment',
            vpc=vpc,
            vpc_subnets=SubnetSelection(
                subnet_type=SubnetType.PUBLIC,
            ),
            compute_environment_name='AnvilFileTransferCompute',
            maxv_cpus=2
        )

        job_queue = JobQueue(
            self,
            'JobQueue',
            job_queue_name='AnvilFileTransferJobQueue',
        )

        job_queue.add_compute_environment(
            compute_environment,
            1
        )

        job_role = Role(
            self,
            'AnvilFileTransferJobRole',
            assumed_by=ServicePrincipal(
                'ecs-tasks.amazonaws.com'
            )
        )

        anvil_file_transfer_secrets = SMSecret.from_secret_complete_arn(
            self,
            'AnvilFileTransferSecrets',
            'arn:aws:secretsmanager:us-west-2:920073238245:secret:anvil-file-transfer-secrets-sandbox-t555J4',
        )

        container = EcsFargateContainerDefinition(
            self,
            'AnvilFileTransferContainer',
            assign_public_ip=True,
            image=ContainerImage.from_asset(
                './docker',
                platform=Platform.LINUX_AMD64,
            ),
            memory=Size.mebibytes(2048),
            cpu=1,
            environment={},
            secrets={
                'SA_SECRET': Secret.from_secrets_manager(
                    secret=anvil_file_transfer_secrets,
                    field='google_sa_base64',
                ),
                'PORTAL_KEY': Secret.from_secrets_manager(
                    secret=anvil_file_transfer_secrets,
                    field='portal_key',
                ),
                'PORTAL_SECRET_KEY': Secret.from_secrets_manager(
                    secret=anvil_file_transfer_secrets,
                    field='portal_secret_key',
                )
            },
            logging=LogDriver.aws_logs(
                stream_prefix='anvil-file-transfer',
                mode=AwsLogDriverMode.NON_BLOCKING,
                log_retention=RetentionDays.ONE_MONTH,
            )
        )

        job_definition = EcsJobDefinition(
            self,
            'AnvilFileTransferJobDef',
            container=container,
        )

        rule = Rule(
            self,
            'AnvilFileTransferSchedule',
            schedule=Schedule.cron(
                minute='0',
                hour='9',
                day='*',
                month='*',
                year='*'
            ),
        )

        target = BatchJob(
            job_queue_arn=job_queue.job_queue_arn,
            job_queue_scope=job_queue,
            job_definition_arn=job_definition.job_definition_arn,
            job_definition_scope=job_definition,
            job_name='AnvilFileTransferBatchJob',
            retry_attempts=0,
        )

        rule.add_target(target)

        connection = Connection.from_event_bus_arn(
            self,
            'Connection',
            connection_arn='arn:aws:events:us-west-2:920073238245:connection/AwsIgvfStagingSlackWebhookConnectionA9DB5B71-w2HHlMDVlHoo/a3cc9e4f-5c65-421d-b204-d7c83b6d4c12',
            connection_secret_arn='arn:aws:secretsmanager:us-west-2:920073238245:secret:events!connection/AwsIgvfStagingSlackWebhookConnectionA9DB5B71-w2HHlMDVlHoo/1fed33df-4b08-4e7b-9e3b-88f9add600a1-EumdKc',
        )

        endpoint = StringParameter.from_string_parameter_name(
            self,
            'SlackWebhookUrl',
            string_parameter_name='SLACK_WEBHOOK_URL_FOR_AWS_IGVF_STAGING_CHANNEL',
        )

        api_destination = ApiDestination(
            self,
            'AnvilFileTransferSlackNotification',
            connection=connection,
            endpoint=endpoint.string_value,
        )

        succeeded_transformed_event = RuleTargetInput.from_object(
            {
                'text': f':white_check_mark: *AnvilFileTransferSucceeded* | {job_queue.job_queue_arn}'
            }
        )

        failed_transformed_event = RuleTargetInput.from_object(
            {
                'text': f':x: *AnvilFileTransferFailed* | {job_queue.job_queue_arn}'
            }
        )

        succeeded_outcome_notification_rule = Rule(
            self,
            'NotifySlackAnvilFileTransferSucceeded',
            event_pattern=EventPattern(
                source=['aws.batch'],
                detail_type=['Batch Job State Change'],
                detail={
                    'status': ['SUCCEEDED'],
                    'jobQueue': [f'{job_queue.job_queue_arn}'],
                }
            ),
            targets=[
                TargetApiDestination(
                    api_destination=api_destination,
                    event=succeeded_transformed_event,
                )
            ]
        )

        failed_outcome_notification_rule = Rule(
            self,
            'NotifySlackAnvilFileTransferFailed',
            event_pattern=EventPattern(
                source=['aws.batch'],
                detail_type=['Batch Job State Change'],
                detail={
                    'status': ['FAILED'],
                    'jobQueue': [f'{job_queue.job_queue_arn}'],
                }
            ),
            targets=[
                TargetApiDestination(
                    api_destination=api_destination,
                    event=failed_transformed_event,
                )
            ]
        )
