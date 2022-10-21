import React from 'react';
import { Button, Modal, Table } from "react-bootstrap";

const ModalTweets = (props) => {

    return (
        <Modal show={props.show} onHide={() => props.setShow(false)} dialogClassName={"modal-graph"}>
            <Modal.Header closeButton>
                <Modal.Title>Tweets</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Tweet</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {props.tweets.map((tweet, index) => (
                            <tr key={index}>
                                <td>{index}</td>
                                <td>{tweet._source.clean_text}</td>
                                <td>{tweet._score}</td>
                            </tr>
                        ))}
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

export default ModalTweets;