import * as React from 'react';

import { RouteComponentProps } from 'react-router-dom';

import withCountyState from 'component/withCountyState';
import withPoll from 'component/withPoll';

import counties from 'data/counties';

import MissedDeadlinePage from './MissedDeadlinePage';
import CountyDashboardPage from './Page';

import finishAudit from 'action/county/finishAudit';

import allRoundsCompleteSelector from 'selector/county/allRoundsComplete';
import auditCompleteSelector from 'selector/county/auditComplete';
import auditStartedSelector from 'selector/county/auditStarted';
import canAuditSelector from 'selector/county/canAudit';
import canRenderReportSelector from 'selector/county/canRenderReport';
import canSignInSelector from 'selector/county/canSignIn';
import currentRoundNumberSelector from 'selector/county/currentRoundNumber';
import missedDeadlineSelector from 'selector/county/missedDeadline';

interface MatchParams {
    id: string;
}

interface DashboardProps extends RouteComponentProps<MatchParams> {
    allRoundsComplete: boolean;
    auditComplete: boolean;
    auditStarted: boolean;
    canAudit: boolean;
    canRenderReport: boolean;
    canSignIn: boolean;
    countyState: County.AppState;
    currentRoundNumber: number;
    missedDeadline: boolean;
}

class CountyDashboardContainer extends React.Component<DashboardProps> {
    public render() {
        const {
            allRoundsComplete,
            auditStarted,
            canAudit,
            canRenderReport,
            canSignIn,
            countyState,
            history,
            match,
            missedDeadline,
        } = this.props;

        if (!countyState) {
            return <div />;
        }

        if (missedDeadline) {
            return <MissedDeadlinePage />;
        }

        if (!countyState.id) {
            return <div />;
        }

        const boardIndex = parseInt(match.params.id, 10);

        const countyInfo = counties[countyState.id];
        const startAudit = () =>
            history.push('/county/audit/' + boardIndex);

        const props = {
            allRoundsComplete,
            auditStarted,
            canAudit,
            canRenderReport,
            canSignIn,
            countyInfo,
            finishAudit,
            startAudit,
            ...this.props,
        };

        return <CountyDashboardPage { ...props } />;
    }
}

function mapStateToProps(countyState: County.AppState) {
    return {
        allRoundsComplete: allRoundsCompleteSelector(countyState),
        auditComplete: auditCompleteSelector(countyState),
        auditStarted: auditStartedSelector(countyState),
        canAudit: canAuditSelector(countyState),
        canRenderReport: canRenderReportSelector(countyState),
        canSignIn: canSignInSelector(countyState),
        countyState,
        currentRoundNumber: currentRoundNumberSelector(countyState),
        missedDeadline: missedDeadlineSelector(countyState),
    };
}

export default withPoll(
    withCountyState(CountyDashboardContainer),
    'COUNTY_DASHBOARD_POLL_START',
    'COUNTY_DASHBOARD_POLL_STOP',
    mapStateToProps,
);
