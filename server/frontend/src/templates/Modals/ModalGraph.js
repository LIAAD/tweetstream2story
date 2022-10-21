import React from 'react';
import {Col, Modal, Row} from "react-bootstrap";
import DRSGraph from "../Tabs/DRSGraph";

const ModalGraph = (props) => {
    return (
        <Modal show={props.show} onHide={() => props.setShow(false)} dialogClassName={"modal-graph"}>
            <Modal.Header closeButton>
                <Modal.Title>Knowledge Graph</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Row className={"justify-content-center"}>
                    <Col xs={10}>
                        <DRSGraph
                            actors_dict={props.results.actors_dict}
                            events_dict={props.results.events_dict}
                            ann_str={props.results.ann_str}
                            event_relations={props.results.event_relations}
                            non_event_relations={props.results.non_event_relations}
                            new_actors = {props.results.new_actors || []} // only used for tweet2story
                        />
                    </Col>
                </Row>
            </Modal.Body>
        </Modal>
    );
};

export default ModalGraph;