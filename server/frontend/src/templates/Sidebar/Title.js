import { Col, Nav, Navbar, Row } from "react-bootstrap";
import { Link } from "react-router-dom";

const Title = (props) => {
  return (
    <>
      <Col className="d-lg-none pt-5 text-center">
        <Navbar collapseOnSelect expand="lg">
          <Link to="/" className="font-lg ps-2 ps-md-4">Tweet2Story</Link>
          <Navbar.Toggle aria-controls="responsive-navbar-nav" />
          <Navbar.Collapse id="responsive-navbar-nav" className="pt-3">
            <Nav className="mr-auto">
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
            </Nav>
          </Navbar.Collapse>
        </Navbar>
      </Col>
      <Row className="d-none padding-top-header d-lg-flex font-lg align-items-center">
        <Col lg={3} className="ps-5">
          <Link to="/">TweetStream2Story</Link>
        </Col>
        <Col className="ps-0">{props.title}</Col>
      </Row>
    </>
  );
};

export default Title;
