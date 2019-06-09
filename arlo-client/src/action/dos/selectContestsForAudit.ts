import { endpoint } from 'config';

import createSubmitAction from 'action/createSubmitAction';

import { format } from 'adapter/contestsForAudit';

const url = endpoint('select-contests');

const selectContestsForAudit = createSubmitAction({
    failType: 'SELECT_CONTESTS_FOR_AUDIT_FAIL',
    networkFailType: 'SELECT_CONTESTS_FOR_AUDIT_NETWORK_FAIL',
    okType: 'SELECT_CONTESTS_FOR_AUDIT_OK',
    sendType: 'SELECT_CONTESTS_FOR_AUDIT_SEND',
    url,
});

export default (data: DOS.Form.SelectContests.FormData) =>
    selectContestsForAudit(format(data));
