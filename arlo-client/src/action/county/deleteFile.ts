import action from 'action';
import { endpoint } from 'config';
import { empty } from 'projectutil';

const deleteFileUrl = endpoint('delete-file');

async function deleteFile(fileType: string) {
    const init: RequestInit = {
        body: JSON.stringify( { fileType } ),
        credentials: 'include',
        method: 'post',
    };

    try {
        action('DELETE_FILE_SEND', { fileType });

        const r = await fetch(deleteFileUrl, init);

        const received = await r.json().catch(empty);

        if (!r.ok) {
            action('DELETE_FILE_FAIL', { fileType, received });
            return false;
        }

        action('DELETE_FILE_OK', { fileType, received });
        return true;

    } catch (e) {
        action('DELETE_FILE_NETWORK_FAIL', { fileType });

        throw e;
    }
}

export default deleteFile;
