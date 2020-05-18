import * as cdk from '@aws-cdk/core';
import * as ddb from '@aws-cdk/aws-dynamodb';
import * as api from '@aws-cdk/aws-apigateway';

export class PinpointUrlClickStreamServiceStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    const aliasTable = new ddb.Table(this, 'AliasTable', {
      partitionKey: {name: 'id', type: ddb.AttributeType.NUMBER}
    });




  }
}
