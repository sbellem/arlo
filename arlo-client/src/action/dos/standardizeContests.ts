import { endpoint } from 'config';

import { format } from 'adapter/standardizeContests';

import action from 'action';
import createSubmitAction from 'action/createSubmitAction';

const url = endpoint('set-contest-names');

export default (
    contests: DOS.Contests,
    data: DOS.Form.StandardizeContests.FormData,
) => {
    const submitAction = createSubmitAction({
        failType: 'STANDARDIZE_CONTESTS_FOR_AUDIT_FAIL',
        networkFailType: 'STANDARDIZE_CONTESTS_FOR_AUDIT_NETWORK_FAIL',
        okType: 'STANDARDIZE_CONTESTS_FOR_AUDIT_OK',
        sendType: 'STANDARDIZE_CONTESTS_FOR_AUDIT_SEND',
        url,
    });

    action('STANDARDIZE_CONTESTS_FOR_AUDIT');
    submitAction(format(contests, data));
};
