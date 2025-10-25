
import React, {useState} from 'react';

export default function UploadPage({apiBase}){
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  async function submit(e){
    e.preventDefault();
    if(!file) return alert('Pick image');
    const fd = new FormData();
    fd.append('image', file);
    const res = await fetch(apiBase + '/predict', {method:'POST', body: fd});
    const json = await res.json();
    setResult(json);
  }
  return (
    <div>
      <h2>Upload (Quick test)</h2>
      <form onSubmit={submit}>
        <input type="file" accept="image/*" onChange={e=>setFile(e.target.files[0])}/>
        <button>Upload</button>
      </form>
      <pre>{result ? JSON.stringify(result, null, 2) : 'No result yet'}</pre>
    </div>
  );
}
