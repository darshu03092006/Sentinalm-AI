export default function App() {
  return (
    <div
      style={{
        background: "#050816",
        minHeight: "100vh",
        color: "white",
        padding: "20px",
        fontFamily: "Arial",
      }}
    >
      <h1
        style={{
          color: "#00ffcc",
          textAlign: "center",
          marginBottom: "20px",
        }}
      >
        SENTINEL AI SURVEILLANCE SYSTEM
      </h1>

      <div
        style={{
          border: "2px solid #00ffcc",
          borderRadius: "20px",
          overflow: "hidden",
          width: "90%",
          margin: "auto",
          boxShadow: "0 0 20px #00ffcc",
        }}
      >
        <img
          src="http://127.0.0.1:8000/video_feed"
          alt="Live Feed"
          style={{
            width: "100%",
            display: "block",
          }}
        />
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          marginTop: "20px",
        }}
      >
        <div
          style={{
            background: "#111827",
            padding: "20px",
            borderRadius: "15px",
            width: "200px",
            textAlign: "center",
            boxShadow: "0 0 10px #00ffcc",
          }}
        >
          <h2>People</h2>
          <p style={{ color: "#00ffcc", fontSize: "30px" }}>18</p>
        </div>

        <div
          style={{
            background: "#111827",
            padding: "20px",
            borderRadius: "15px",
            width: "200px",
            textAlign: "center",
            boxShadow: "0 0 10px red",
          }}
        >
          <h2>Threats</h2>
          <p style={{ color: "red", fontSize: "30px" }}>5</p>
        </div>
      </div>
    </div>
  );
}