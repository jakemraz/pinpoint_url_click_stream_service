import { expect as expectCDK, matchTemplate, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import * as PinpointUrlClickStreamService from '../lib/pinpoint_url_click_stream_service-stack';

test('Empty Stack', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new PinpointUrlClickStreamService.PinpointUrlClickStreamServiceStack(app, 'MyTestStack');
    // THEN
    expectCDK(stack).to(matchTemplate({
      "Resources": {}
    }, MatchStyle.EXACT))
});
