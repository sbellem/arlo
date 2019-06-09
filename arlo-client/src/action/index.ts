import store from 'store';

export default function action<D>(type: string, data: (D | {}) = {}) {
    store.dispatch({ data, type });
}
