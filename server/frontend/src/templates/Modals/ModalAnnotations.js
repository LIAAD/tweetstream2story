import React from 'react';
import {Button, Modal, Table} from "react-bootstrap";

const ModalAnnotations = (props) => {

    return (
        <Modal show={props.show} onHide={() => props.setShow(false)} dialogClassName={"modal-graph"}>
            <Modal.Header closeButton>
                <Modal.Title>Annotations</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Annotation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {props.results.ann_str && 
                        <>
                            {props.results.ann_str.map((ann, index) => (
                            <tr key={index}>
                                <td>{ann}</td>
                            </tr>
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

export default ModalAnnotations;