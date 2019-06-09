import * as React from 'react';

import LicenseFooter from 'component/LicenseFooter';

interface Props {
    main: React.ReactNode;
}

const LoginLayout = (props: Props) => {
    return (
        <div className='l-wrapper'>
            <div className='l-main'>
                { props.main }
            </div>
            <LicenseFooter />
        </div>
    );
};

export default LoginLayout;
