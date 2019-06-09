import * as React from 'react';

import { Button, Intent } from '@blueprintjs/core';

import fetchReport from 'action/dos/fetchReport';
import startNextRound from 'action/dos/startNextRound';

interface ControlProps {
    canRenderReport: boolean;
    currentRound: number;
}

const Control = (props: ControlProps) => {
    const {
        canRenderReport,
        currentRound,
    } = props;

    return (
        <div className='state-dashboard-round'>
            <div>
                <h4>Round { currentRound } completed</h4>
                <Button intent={ Intent.PRIMARY }
                        onClick={ startNextRound }>
                    Start round { currentRound + 1 }
                </Button>
            </div>
            <div>
                <Button large
                        disabled={ !canRenderReport }
                        intent={ Intent.PRIMARY }
                        icon='import'
                        onClick={ fetchReport }>
                    Download audit report
                </Button>
            </div>
        </div>
    );
};

export default Control;
