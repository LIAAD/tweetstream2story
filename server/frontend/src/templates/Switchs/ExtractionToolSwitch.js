import React from 'react';
import {Col, Form, Row} from "react-bootstrap";

const ExtractionToolSwitch = (props) => {
    return (
        <Form.Group as={Row} className={"mb-3 ms-1"}>
            <Col>
                <Form.Label>{props.name}</Form.Label>
            </Col>
            <Col className={"text-center"}>
                <Form.Check
                    type="switch"
                    defaultChecked={true}
                    onChange={event => props.changeTool(props.name)}
                />
            </Col>
        </Form.Group>
    );
};

export default ExtractionToolSwitch;