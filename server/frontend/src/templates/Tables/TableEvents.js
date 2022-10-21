import { Table } from "react-bootstrap";

const TableAnnotations = (props) => {

    return (
        <Table striped bordered hover>
            <thead>
                <tr>
                    <th>Events</th>
                </tr>
            </thead>
            <tbody>
                {props.drs_str &&
                    <>
                        {props.drs_str.split("\n").map((event, index) => (
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
    )
};

export default TableAnnotations;
