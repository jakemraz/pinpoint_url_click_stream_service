#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { PinpointUrlClickStreamServiceStack } from '../lib/pinpoint_url_click_stream_service-stack';

const app = new cdk.App();
new PinpointUrlClickStreamServiceStack(app, 'PinpointUrlClickStreamServiceStack');
