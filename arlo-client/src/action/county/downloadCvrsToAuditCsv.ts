import { endpoint } from 'config';

export default (round: number) => {
    const params = `round=${round}`;
    const url = `${endpoint('cvr-to-audit-download')}?${params}`;

    window.location.replace(url);
};
