import * as React from 'react';

import CountyLayout from 'component/CountyLayout';

import CountyAuditWizardContainer from './Wizard/Container';

interface Props {
    reviewingBallotId?: number;
}

const CountyAuditPage = (props: Props) => {
    const { reviewingBallotId } = props;

    const main =
        <CountyAuditWizardContainer reviewingBallotId={ reviewingBallotId } />;

    return <CountyLayout main={ main } />;
};

export default CountyAuditPage;
