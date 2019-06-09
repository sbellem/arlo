import * as React from 'react';
import { Redirect } from 'react-router-dom';

import { History } from 'history';

import withDOSState from 'component/withDOSState';
import withSync from 'component/withSync';

import ReviewPage from './ReviewPage';

import publishBallotsToAudit from 'action/dos/publishBallotsToAudit';

interface ContainerProps {
    history: History;
    dosState: DOS.AppState;
}

class ReviewPageContainer extends React.Component<ContainerProps> {
    public render() {
        const { history, dosState } = this.props;

        if (!dosState) {
            return <div />;
        }

        if (!dosState.asm) {
            return <div />;
        }

        if (dosState.asm === 'DOS_AUDIT_ONGOING') {
            return <Redirect to='/sos' />;
        }

        const props = {
            back: () => history.push('/sos/audit/seed'),
            dosState,
            publishBallotsToAudit,
            saveAndDone: () => history.push('/sos'),
        };

        return <ReviewPage { ...props } />;
    }
}

function mapStateToProps(dosState: DOS.AppState) {
    return { dosState };
}

export default withSync(
    withDOSState(ReviewPageContainer),
    'DOS_DEFINE_AUDIT_REVIEW_SYNC',
    mapStateToProps,
);
