import * as cdk from '@aws-cdk/core';
import * as ddb from '@aws-cdk/aws-dynamodb';
import * as apigw from '@aws-cdk/aws-apigateway';
import * as lambda from '@aws-cdk/aws-lambda';
import * as path from 'path';

export class PinpointUrlClickStreamServiceStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    const aliasTable = new ddb.Table(this, 'AliasTable', {
      partitionKey: {name: 'id', type: ddb.AttributeType.NUMBER}
    });

    const campaignFunction = new lambda.Function(this, 'CampaignFunction', {
      runtime: lambda.Runtime.PYTHON_3_8,
      handler: 'campaign.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda-handler')),
      environment: {
        TABLE_NAME: aliasTable.tableName
      }
    });
    aliasTable.grantFullAccess(campaignFunction);
    
    

    const api = new apigw.LambdaRestApi(this, 'ApiGateway', {
      handler: campaignFunction
    });



  }
}
