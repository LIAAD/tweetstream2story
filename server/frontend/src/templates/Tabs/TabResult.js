import {Col, Nav, Row, Tab} from "react-bootstrap";

const TabResult = (props) => {

    const parsedDrsStr = props.drs_str.split("\n");

    return (
        <Tab.Container defaultActiveKey="first">
            <Row id="results-tab">
                <Col sm={3}>
                    <Nav variant="pills">
                        <Nav.Item className="mx-auto w-100 text-center mb-3">
                            <Nav.Link
                                eventKey="first"
                                className="font-color-background-color"
                            >
                                ANN Text
                            </Nav.Link>
                        </Nav.Item>
                        <Nav.Item className="mx-auto w-100 text-center mb-3">
                            <Nav.Link
                                eventKey="second"
                                className="font-color-background-color"
                            >
                                DRS Text
                            </Nav.Link>
                        </Nav.Item>
                        <Nav.Item className="mx-auto w-100 text-center mb-3">
                            <Nav.Link
                                eventKey="third"
                                className="font-color-background-color"
                                onClick={event => props.setShow(true)}
                            >
                                Graph
                            </Nav.Link>
                        </Nav.Item>
                        <Nav.Item className="mx-auto w-100 text-center mb-3">
                            <Nav.Link
                                eventKey="fourth"
                                className="font-color-background-color"
                            >
                                Input Text
                            </Nav.Link>
                        </Nav.Item>
                    </Nav>
                </Col>
                <Col sm={9}>
                    <Tab.Content>
                        <Tab.Pane eventKey="first">
                            {props.ann_str.map((elem, index) => (
                                <p key={index}>{elem}</p>
                            ))}
                        </Tab.Pane>
                        <Tab.Pane eventKey="second">
                            {parsedDrsStr.map((elem, index) => (
                                <p key={index}>{elem}</p>
                            ))}
                        </Tab.Pane>
                        <Tab.Pane eventKey="fourth">{props.input_text}</Tab.Pane>
                    </Tab.Content>
                </Col>
            </Row>
        </Tab.Container>
    );
};

export default TabResult;
