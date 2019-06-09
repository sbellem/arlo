import action from 'action';
import { endpoint } from 'config';
import { empty } from 'projectutil';

const deleteFileUrl = endpoint('delete-file');

async function deleteFileForCounty(fileType: string, countyId: number) {
    const init: RequestInit = {
        body: JSON.stringify( { fileType, countyId } ),
        credentials: 'include',
        method: 'post',
    };

    try {
        action('DOS_DELETE_FILE_SEND', { fileType, countyId });

        const r = await fetch(deleteFileUrl, init);

        const received = await r.json().catch(empty);

        if (!r.ok) {
            action('DOS_DELETE_FILE_FAIL', { fileType, received });
            return false;
        }

        action('DOS_DELETE_FILE_OK', { fileType, countyId, received });
        return true;

    } catch (e) {
        action('DOS_DELETE_FILE_NETWORK_FAIL', { fileType, countyId });

        throw e;
    }
}

export default deleteFileForCounty;
