import withDOSState from 'component/withDOSState';
import withSync from 'component/withSync';

import OverviewPage from './OverviewPage';

function mapStateToProps(dosState: DOS.AppState) {
    return {
        contests: dosState.contests,
        dosState,
    };
}

export default withSync(
    withDOSState(OverviewPage),
    'DOS_CONTEST_OVERVIEW_SYNC',
    mapStateToProps,
);
