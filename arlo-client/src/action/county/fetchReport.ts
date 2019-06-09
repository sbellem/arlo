import { endpoint } from 'config';

const url = endpoint('county-report');

export default () => window.location.replace(url);
