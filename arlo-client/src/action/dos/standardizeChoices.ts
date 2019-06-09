import { endpoint } from 'config';

import { format } from 'adapter/standardizeChoices';

import createSubmitAction from 'action/createSubmitAction';

const url = endpoint('set-contest-names');

export default (
    contests: DOS.Contests,
    data: DOS.Form.StandardizeChoices.FormData,
) => {
    const action = createSubmitAction({
        failType: 'STANDARDIZE_CHOICES_FOR_AUDIT_FAIL',
        networkFailType: 'STANDARDIZE_CHOICES_FOR_AUDIT_NETWORK_FAIL',
        okType: 'STANDARDIZE_CHOICES_FOR_AUDIT_OK',
        sendType: 'STANDARDIZE_CHOICES_FOR_AUDIT_SEND',
        url,
    });

    action(format(contests, data));
};
