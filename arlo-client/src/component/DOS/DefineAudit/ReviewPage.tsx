import * as React from 'react';

import * as _ from 'lodash';

import { Breadcrumb, Button, Card, Intent } from '@blueprintjs/core';

import DOSLayout from 'component/DOSLayout';
import counties from 'data/counties';
import { formatLocalDate } from 'date';

const Breadcrumbs = () => (
    <ul className='pt-breadcrumbs mb-default'>
        <li><Breadcrumb href='/sos' text='SoS' />></li>
        <li><Breadcrumb href='/sos/audit' text='Audit Admin' /></li>
        <li><Breadcrumb className='pt-breadcrumb-current' text='Review' /></li>
    </ul>
);

function formatReason(reason: AuditReason): string {
    if (reason === 'STATE_WIDE_CONTEST') {
        return 'State Contest';
    }

    return 'County Contest';
}

interface SelectedContestsProps {
    auditedContests: DOS.AuditedContests;
    contests: DOS.Contests;
}

const SelectedContests = (props: SelectedContestsProps) => {
    const { auditedContests, contests } = props;

    const rows = _.map(props.auditedContests, audited => {
        const contest = contests[audited.id];
        const countyName = counties[contest.countyId].name;

        return (
            <tr key={ contest.id }>
                <td>{ countyName }</td>
                <td>{ contest.name }</td>
                <td>{ formatReason(audited.reason) }</td>
            </tr>
        );
    });

    return (
        <Card>
            <h3>Selected Contests</h3>
            <Card>
                <table className='pt-html-table pt-html-table-bordered pt-small'>
                    <thead>
                        <tr>
                            <th>County</th>
                            <th>Name</th>
                            <th>Reason</th>
                        </tr>
                    </thead>
                    <tbody>
                        { rows }
                    </tbody>
                </table>
            </Card>
        </Card>
    );
};

interface AuditReviewProps {
    back: OnClick;
    publishBallotsToAudit: OnClick;
    saveAndDone: OnClick;
    dosState: DOS.AppState;
}

function riskLimitPercent(dosState: DOS.AppState) {
    return (dosState.riskLimit! * 100).toFixed(2);
}

const AuditReview = (props: AuditReviewProps) => {
    const { back, publishBallotsToAudit, saveAndDone, dosState } = props;

    const launch = () => {
        publishBallotsToAudit();
        saveAndDone();
    };

    const disableLaunchButton = !dosState.seed;

    const main =
        <div>
            <Breadcrumbs />
            <h2>Audit</h2>
            <h3>Audit Definition Review</h3>
            <div>
                This is the set of audit data which will be used to define the list of
                ballots to audit for each county. Once this is submitted, it will be released
                to the counties and the previous pages will not be editable.
                In particular, you will not be able to change which contests are under audit.
            </div>
            <Card>
                <table className='pt-html-table'>
                    <tbody>
                        <tr>
                            <td>Public Meeting Date:</td>
                            <td>{ dosState.publicMeetingDate
                                  && formatLocalDate(dosState.publicMeetingDate) }</td>
                        </tr>
                        <tr>
                            <td>Election Date:</td>
                            <td>{ dosState.election && dosState.election.date
                                  && formatLocalDate(dosState.election.date) }</td>
                        </tr>
                        <tr>
                            <td>Election Type:</td>
                            <td>{ dosState.election && dosState.election.type }</td>
                        </tr>
                        <tr>
                            <td>Risk Limit:</td>
                            <td>{ riskLimitPercent(dosState) }%</td>
                        </tr>
                        <tr>
                            <td>Random Number Generator Seed:</td>
                            <td>{ dosState.seed }</td>
                        </tr>
                    </tbody>
                </table>
            </Card>
            <SelectedContests auditedContests={ dosState.auditedContests }
                              contests={ dosState.contests } />
            <div>
                <Button onClick={ back }>Back</Button>
                <Button className='ml-default'
                        disabled={ disableLaunchButton }
                        intent={ Intent.PRIMARY }
                        onClick={ launch }>
                    Launch Audit
                </Button>
            </div>
        </div>;

    return <DOSLayout main={ main } />;
};

export default AuditReview;
