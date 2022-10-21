import { Col } from "react-bootstrap";
import { Link } from "react-router-dom";

const Sidebar = (props) => {
  return (
    <>
      <Col lg={3} className="d-none d-lg-block ps-5 font-lg">
      <div className="mb-3">
          <Link to="/about">About</Link>
        </div>
        <div className="mb-3">
          <Link to="/">Demo</Link>
        </div>
        <div className="mb-3">
          <Link to="/examples">Examples</Link>
        </div>
        <div className="mb-3">
          <a href="https://github.com/LIAAD/tweetstream2story">Open Source</a>
        </div>
      </Col>
    </>
  );
};

export default Sidebar;
