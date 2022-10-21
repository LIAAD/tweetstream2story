import React from 'react';
import {Button, Col, Form, Modal, Row} from "react-bootstrap";
import ExtractionToolSwitch from "../Switchs/ExtractionToolSwitch";

const ModalDemo = (props) => {

    const changeTool = (tool) => {
        props.setValues((values) => ({
            ...values,
            tools: {
                ...values.tools,
                [tool]: !values.tools[tool]
            }
        }));
    }

    return (
        <Modal show={props.show} values={props.values} onHide={() => props.setShow(false)} size="xl" dialogClassName="my-modal">
            <Modal.Header closeButton>
                <Modal.Title>Select The Extraction Tools</Modal.Title>
            </Modal.Header>
            <Modal.Body className={"pb-3 align-center"}>
                <Row>
                    <Col>
                        <h5 className={"text-center"}>Participants Extraction</h5>
                        <hr/>
                        <Form>
                            {props.values.lang === 'en' &&
                                <ExtractionToolSwitch name={"NLTK"} changeTool={changeTool}/>}
                            <ExtractionToolSwitch name={"spaCy"} changeTool={changeTool}/>
                        </Form>
                    </Col>
                    <Col>
                        <h5 className={"text-center"}>Temporal Extraction</h5>
                        <hr/>
                        <Form>
                            <ExtractionToolSwitch name={"py_heideltime"} changeTool={changeTool}/>
                        </Form>
                    </Col>
                    <Col>
                        <h5 className={"text-center"}>Events Extraction</h5>
                        <hr/>
                        <Form>
                            <ExtractionToolSwitch name={"AllenNLP"} changeTool={changeTool}/>
                        </Form>
                    </Col>
                </Row>
                <Row className={"mt-5 justify-content-center"}>
                    {props.values.lang === 'en' && <Col xs={5}>
                        <h5 className={"text-center"}>Objectal Linking Resolution</h5>
                        <hr/>
                        <Form>
                            <ExtractionToolSwitch name={"Spacy (Objectal Linking)"} changeTool={changeTool}/>
                        </Form>
                    </Col>}
                    <Col xs={5}>
                        <h5 className={"text-center"}>Sematic Role Labeling</h5>
                        <hr/>
                        <Form>
                            <ExtractionToolSwitch name={"AllenNLP (Sematic Role Labeling)"} changeTool={changeTool}/>
                        </Form>
                    </Col>
                </Row>
            </Modal.Body>
            <Modal.Footer>
                <Button variant={"outline-dark"} onClick={props.handleSubmit}>Submit</Button>
            </Modal.Footer>
        </Modal>
    )
};

export default ModalDemo;