import { useState } from "react";
import { Alert, Button, Col, Form, Modal, Row } from "react-bootstrap";

const ModalRealTime = (props) => {

    const modes = {
        NOW: "1",
        FUTURE: "2",
        PAST: "3",
    }

    const formatDatetime = (datetime) => {
        let dd = datetime.getDate(); // day of the month
        let MM = datetime.getMonth() + 1; // getMonth() is zero-based
        let hh = datetime.getHours();
        let mm = datetime.getMinutes();

        return [datetime.getFullYear(), '-',
        (MM > 9 ? '' : '0') + MM, '-',
        (dd > 9 ? '' : '0') + dd,
            'T',
        (hh > 9 ? '' : '0') + hh, ':',
        (mm > 9 ? '' : '0') + mm
        ].join('');
    }

    const [mode, setMode] = useState(modes.NOW)
    const [consumerKey, setConsumerKey] = useState("")
    const [consumerSecret, setConsumerSecret] = useState("")
    const [startDate, setStartDate] = useState(formatDatetime(new Date()));
    const [endDate, setEndDate] = useState(formatDatetime(new Date(new Date().getTime() + 60 * 60 * 1000)));
    const [timeInterval, setTimeInterval] = useState(10);
    const [timeUnit, setTimeUnit] = useState("minutes");
    const [lang, setLang] = useState("en");

    const handleSubmit = (e) => {

        e.preventDefault();
        const now = new Date();

        // Validate dates
        if (mode === modes.FUTURE && (
            (new Date(endDate) <= new Date(startDate)) ||
            (new Date(startDate) < new Date()))) {
            return;
        }

        else if (mode === modes.PAST && (
            (new Date(endDate) <= new Date(startDate)) ||
            (new Date(startDate) >= new Date()) ||
            (new Date(endDate) >= new Date()))) {
            return;
        }

        let requestBody = {
            "startDate": mode === modes.NOW
                ? now.toISOString().split('.')[0] + 'Z'
                : new Date(startDate).toISOString().split('.')[0] + 'Z',
            "endDate": mode === modes.NOW
                ? new Date(now.getTime() + 86400000).toISOString().split('.')[0] + 'Z'
                : new Date(endDate).toISOString().split('.')[0] + 'Z',
            "timeInterval": parseInt(timeInterval),
            "timeUnit": timeUnit,
            "lang": lang,
            "mode": mode,
            "consumerKey": consumerKey,
            "consumerSecret": consumerSecret
        }

        // Don't send startDate and endDate if mode == now
        const dateModes = [modes.FUTURE, modes.PAST]

        props.submitCallback(requestBody)
    }

    const handleEntered = () => {
        setStartDate(formatDatetime(new Date()));
        setEndDate(formatDatetime(new Date(new Date().getTime() + 60 * 60 * 1000)));
    }

    return (
        <Modal show={props.show} onEntered={handleEntered} onHide={() => props.setShowModal(false)} size="xl">

            <Form noValidate onSubmit={handleSubmit}>
                <Modal.Header closeButton>
                    <Modal.Title>Options</Modal.Title>
                </Modal.Header>

                <Modal.Body className={"pb-3 align-center"}>

                    <Form.Group className="mb-3">
                        <Form.Label> Language </Form.Label>
                        <Form.Select
                            type="select"
                            value={lang}
                            onChange={(e) => setLang(e.target.value)}
                        >
                            <option value="en">🇬🇧 EN</option>
                            <option value="pt">🇵🇹 PT</option>
                        </Form.Select>
                    </Form.Group>

                    <Row className="mb-3">
                        <Form.Label> Extract narrative every... </Form.Label>
                        <Form.Group as={Col}>
                            <Form.Control type="number" required value={timeInterval} onChange={(e) => setTimeInterval(e.target.value)}></Form.Control>
                        </Form.Group>
                        <Form.Group as={Col}>
                            <Form.Select
                                type="select"
                                value={timeUnit}
                                onChange={(e) => setTimeUnit(e.target.value)}>
                                <option>minutes</option>
                                <option>hours</option>
                                <option>days</option>
                            </Form.Select>
                        </Form.Group>
                    </Row>

                    <Form.Group className="mb-3">
                        <Form.Select
                            type="select"
                            value={mode}
                            onChange={(e) => setMode(e.target.value)}>
                            <option value={modes.NOW}> Start now    </option>
                            <option value={modes.FUTURE}> Schedule     </option>
                            <option value={modes.PAST} >Past event   </option>
                        </Form.Select>

                    </Form.Group>


                    {mode === modes.FUTURE && (
                        <>
                            <Form.Group className="mb-3">
                                <Form.Label> Start Date </Form.Label>
                                <Form.Control
                                    type="datetime-local"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    isInvalid={new Date(startDate) < new Date()}>
                                </Form.Control>
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label> End Date </Form.Label>
                                <Form.Control
                                    type="datetime-local"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    isInvalid={new Date(endDate) <= new Date(startDate)}>
                                </Form.Control>
                                <Form.Control.Feedback type="invalid">
                                    Topic should end after its start date.
                                </Form.Control.Feedback>
                            </Form.Group>
                        </>
                    )}

                    {mode === modes.PAST && (
                        <>
                            <Form.Group className="mb-3">
                                <Form.Label> Start Date </Form.Label>
                                <Form.Control
                                    type="datetime-local"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    isInvalid={new Date(startDate) >= new Date()}>
                                </Form.Control>
                                <Form.Control.Feedback type="invalid">
                                    Topic should start before current time.
                                </Form.Control.Feedback>
                            </Form.Group>

                            <Form.Group className="mb-3">
                                <Form.Label> End Date </Form.Label>
                                <Form.Control
                                    type="datetime-local"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    isInvalid={(new Date(endDate) >= new Date()) || (new Date(endDate) <= new Date(startDate))}>
                                </Form.Control>
                                <Form.Control.Feedback type="invalid">
                                    Topic should end before current time and after its start date.
                                </Form.Control.Feedback>
                            </Form.Group>

                            <Form.Label> Twitter API Credentials</Form.Label>
                            <Row className="mb-3">
                                <Form.Group as={Col}>
                                    <Form.Control
                                        type="text"
                                        placeholder="Consumer key"
                                        rows={1}
                                        name="text"
                                        value={consumerKey}
                                        onChange={(event) => setConsumerKey(event.target.value)}
                                    />
                                </Form.Group>

                                <Form.Group as={Col}>
                                    <Form.Control
                                        type="text"
                                        placeholder="Consumer secret"
                                        rows={1}
                                        name="text"
                                        value={consumerSecret}
                                        onChange={(event) => setConsumerSecret(event.target.value)}
                                    />
                                </Form.Group>
                                <Form.Text id="passwordHelpBlock" muted>
                                    Your credentials will not be stored.
                                </Form.Text>
                            </Row>
                        </>
                    )}

                </Modal.Body>

                <Modal.Footer>
                    {props.error &&
                        <Alert variant="danger">
                            {props.error}
                        </Alert>
                    }
                    <Button type="submit" variant="outline-dark">Submit</Button>
                </Modal.Footer>
            </Form >

        </Modal >

    )
};

export default ModalRealTime;