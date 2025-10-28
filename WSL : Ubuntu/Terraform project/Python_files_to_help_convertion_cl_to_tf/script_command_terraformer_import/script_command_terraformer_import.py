import yaml

# === Mapping CloudFormation → Terraformer service names ===
CFN_TO_TERRAFORMER = {
    # Réseau / EC2
    "AWS::EC2::Instance": "ec2_instance",
    "AWS::EC2::SecurityGroup": "sg",
    "AWS::EC2::Subnet": "subnet",
    "AWS::EC2::RouteTable": "route_table",
    "AWS::EC2::InternetGateway": "igw",
    "AWS::EC2::NatGateway": "nat",
    "AWS::EC2::VPC": "vpc",
    "AWS::EC2::VPCEndpoint": "vpc_endpoint",
    "AWS::EC2::VPCPeeringConnection": "vpc_peering",
    "AWS::EC2::VPNGateway": "vpn_gateway",
    "AWS::EC2::VPNConnection": "vpn_connection",
    "AWS::EC2::CustomerGateway": "customer_gateway",
    "AWS::EC2::TransitGateway": "transit_gateway",
    "AWS::EC2::TransitGatewayRouteTable": "transit_gateway",
    "AWS::EC2::TransitGatewayVpcAttachment": "transit_gateway",
    "AWS::EC2::NetworkAcl": "nacl",
    "AWS::EC2::EIP": "eip",

    # S3
    "AWS::S3::Bucket": "s3",

    # IAM
    "AWS::IAM::Role": "iam",
    "AWS::IAM::Policy": "iam",
    "AWS::IAM::User": "iam",
    "AWS::IAM::Group": "iam",
    "AWS::IAM::InstanceProfile": "iam",

    # Load Balancers (ALB/NLB)
    "AWS::ElasticLoadBalancingV2::LoadBalancer": "alb",
    "AWS::ElasticLoadBalancingV2::TargetGroup": "alb",
    "AWS::ElasticLoadBalancingV2::Listener": "alb",
    "AWS::ElasticLoadBalancingV2::ListenerRule": "alb",
    "AWS::ElasticLoadBalancing::LoadBalancer": "elb",

    # Lambda
    "AWS::Lambda::Function": "lambda",
    "AWS::Lambda::Permission": "lambda",
    "AWS::Lambda::LayerVersion": "lambda",

    # RDS
    "AWS::RDS::DBInstance": "rds",
    "AWS::RDS::DBCluster": "rds",

    # DynamoDB
    "AWS::DynamoDB::Table": "dynamodb",

    # CloudWatch
    "AWS::CloudWatch::Alarm": "cloudwatch",
    "AWS::Logs::LogGroup": "logs",

    # SNS / SQS
    "AWS::SNS::Topic": "sns",
    "AWS::SNS::Subscription": "sns",
    "AWS::SQS::Queue": "sqs",

    # Route53
    "AWS::Route53::HostedZone": "route53",
    "AWS::Route53::RecordSet": "route53",

    # CloudFront
    "AWS::CloudFront::Distribution": "cloudfront",

    # Config
    "AWS::Config::ConfigRule": "config",

    # Access Analyzer / ACM / KMS / SecretsManager / SecurityHub
    "AWS::AccessAnalyzer::Analyzer": "accessanalyzer",
    "AWS::ACM::Certificate": "acm",
    "AWS::KMS::Key": "kms",
    "AWS::SecretsManager::Secret": "secretsmanager",
    "AWS::SecurityHub::Account": "securityhub",

    # Step Functions
    "AWS::StepFunctions::StateMachine": "sfn",

    # CloudFormation stacks
    "AWS::CloudFormation::Stack": "cloudformation",
}

# Constructeurs YAML pour ignorer les tags CFN comme !Ref, !Sub, etc.
def cloudformation_tag_constructor(loader, node):
    return str(node.value)

cloudformation_tags = [
    '!Ref', '!Sub', '!GetAtt', '!Join', '!FindInMap', '!ImportValue',
    '!If', '!Equals', '!And', '!Or', '!Not', '!Condition',
    '!Select', '!Split', '!Base64', '!Cidr', '!Transform',
    '!GetAZs'
]

for tag in cloudformation_tags:
    yaml.SafeLoader.add_constructor(tag, cloudformation_tag_constructor)

def extract_resource_types(template_path, output_path):
    with open(template_path, 'r') as f:
        template = yaml.safe_load(f)

    resources = template.get('Resources', {})
    terraformer_services = set()
    unknown_types = set()

    for res_name, res_def in resources.items():
        cfn_type = res_def.get('Type')
        if cfn_type:
            service = CFN_TO_TERRAFORMER.get(cfn_type)
            if service:
                terraformer_services.add(service)
            else:
                unknown_types.add(cfn_type)

    with open(output_path, 'w') as f:
        for svc in sorted(terraformer_services):
            f.write(svc + '\n')

        if unknown_types:
            f.write('\n# Types CFN non reconnus :\n')
            for unknown in sorted(unknown_types):
                f.write(unknown + '\n')

        if terraformer_services:
            f.write('\n# === Commande Terraformer Import ===\n')
            f.write('terraformer import aws --resources ')
            f.write(','.join(sorted(terraformer_services)))
            f.write('\n')

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python extract_types.py <template.yaml> <output.txt>")
        sys.exit(1)

    extract_resource_types(sys.argv[1], sys.argv[2])
