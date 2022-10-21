import { Table } from "react-bootstrap";

const TableAnnotations = (props) => {

    return (
        <Table striped bordered hover>
            <thead>
                <tr>
                    <th>Annotation</th>
                </tr>
            </thead>
            <tbody>
                {props.ann_str &&
                    <>
                        {props.ann_str.map((ann, index) => (
                            <tr key={index}>
                                <td>{ann}</td>
                            </tr>
                        ))}
                    </>
                }

            </tbody>
        </Table>
    )
};

export default TableAnnotations;
