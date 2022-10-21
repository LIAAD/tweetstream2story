import React from 'react';
import {Button, Modal, Table} from "react-bootstrap";

const ModalEvents = (props) => {

    return (
        <Modal show={props.show} onHide={() => props.setShow(false)} dialogClassName={"modal-graph"}>
            <Modal.Header closeButton>
                <Modal.Title>Events</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Annotation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {props.results.drs_str && 
                        <>
                            {props.results.drs_str.split("\n").map((event, index) => (
                                <> {event !== "" &&
                                <tr key={index}>
                                    <td>{event}</td>
                                </tr>
                                    }
                                </>
                            ))}
                        </>
                    }   
                        
                    </tbody>
                </Table>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={() => props.setShow(false)}>
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default ModalEvents;