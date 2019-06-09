import * as React from 'react';

import CountyNav from 'component/County/Nav';
import LicenseFooter from 'component/LicenseFooter';

interface Props {
    main: React.ReactNode;
}

const CountyLayout = (props: Props) => {
    return (
        <div className='l-wrapper'>
            <CountyNav />
            <div className='l-main'>
                { props.main }
            </div>
            <LicenseFooter />
        </div>
    );
};

export default CountyLayout;
