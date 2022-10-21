import { Table } from "react-bootstrap";

const TableTweets = (props) => {

    const formatDatetime = (datetime) => {
        // Convert from ISO to local and then to YYYY-MM-DD hh:mm
        datetime = new Date(datetime);
        let dd = datetime.getDate(); // day of the month
        let MM = datetime.getMonth() + 1; // getMonth() is zero-based
        let hh = datetime.getHours();
        let mm = datetime.getMinutes();

        return  [datetime.getFullYear(), '-',
        (MM>9 ? '' : '0') + MM, '-' ,
        (dd>9 ? '' : '0') + dd,
        ' ',
        (hh>9 ? '' : '0') + hh, ':',
        (mm>9 ? '' : '0') + mm
        ].join('');
    }

    return (
        <Table striped bordered hover>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Tweet</th>
                    {/*<th>Date</th>*/}
                    <th>Score</th>
                </tr>
            </thead>
            <tbody>
                {props.tweets.map((tweet, index) => (
                <tr key={index}>
                    <td>{index}</td>
                    <td>{tweet._source.clean_text}</td>
                    <td>{formatDatetime(tweet._source["date"])}</td>
                    {/*<td>{tweet._score}</td>*/}
                </tr>
                ))}
            </tbody>
        </Table>
    )
};

export default TableTweets;