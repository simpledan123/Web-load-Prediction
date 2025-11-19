import { useEffect, useState } from 'react';
import axios from 'axios';

function Community() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 백엔드 API 호출!
    axios.get('http://127.0.0.1:8000/community/feed')
      .then(response => {
        setPosts(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching feed:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>🔥 Keep Community</h2>
        <button style={{ padding: '10px 20px', background: '#00d1b2', color: 'white', border: 'none', borderRadius: '20px', cursor: 'pointer', fontWeight: 'bold' }}>
          + Write Post
        </button>
      </div>

      {loading ? <p>Loading feed...</p> : null}
      {!loading && posts.length === 0 && <div style={{textAlign:'center', padding:'40px', color:'#666'}}>게시글이 없습니다.<br/>첫 글을 작성해보세요!</div>}

      {posts.map(post => (
        <div key={post.id} style={{ background: 'white', borderRadius: '12px', padding: '20px', marginBottom: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 10px 0' }}>{post.title}</h3>
          <p>{post.content}</p>
          <div style={{ marginTop: '15px', color: '#ff6b6b', fontWeight: 'bold' }}>❤️ {post.likes} Likes</div>
        </div>
      ))}
    </div>
  );
}

export default Community;