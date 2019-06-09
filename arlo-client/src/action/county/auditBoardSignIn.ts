import { endpoint } from 'config';

import createSubmitAction from 'action/createSubmitAction';

import { format } from 'adapter/establishBoard';

const url = endpoint('audit-board-sign-in');

const auditBoardSignIn = createSubmitAction({
    failType: 'AUDIT_BOARD_SIGN_IN_FAIL',
    networkFailType: 'AUDIT_BOARD_SIGN_IN_NETWORK_FAIL',
    okType: 'AUDIT_BOARD_SIGN_IN_OK',
    sendType: 'AUDIT_BOARD_SIGN_IN_SEND',
    url,
});

export default (index: number, board: AuditBoard) => {
    auditBoardSignIn(format(index, board));
};
