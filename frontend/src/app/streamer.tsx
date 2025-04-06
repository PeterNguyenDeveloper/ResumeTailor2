// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck

import {useEffect, useState} from "react";
import MarkdownIt from 'markdown-it';

const BACKEND_URL = "http://137.184.12.12:5000"

interface StreamProps {
    file: File,
    jobDescription: string,
    template: string,
    showDownload?: boolean
}

const StreamComponent: React.FC<StreamProps> = ({file, jobDescription, template, showDownload}) => {
    const [html, setHtml] = useState<string>("");
    const md = new MarkdownIt();
    useEffect(() => {
        const formData = new FormData();
        formData.append("resume", file);
        formData.append("job_description", jobDescription);
        formData.append("template", template);
        fetch(`${BACKEND_URL}/api/stream-tailor-resume`, {
            method: "POST",
            body: formData,
        }).then(async (response) => {
            const reader = response.body?.getReader();
            const decoder = new TextDecoder("utf-8");
            let accumulatedMarkdown = "";
            while (reader) {
                const {done, value} = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value);
                accumulatedMarkdown += chunk; // Append the new chunk to the accumulated Markdown
                const generatedHtml = md.render(accumulatedMarkdown); // Convert the accumulated Markdown
                setHtml(generatedHtml); // Update the HTML state
            }
        });
    }, []);
    return (
        <>
            <div className={'overflow-x-auto h-fit'}>
                {
                    !html ?
                        (
                            <p>Loading...</p>
                        )
                        :
                        (
                            <p style={{whiteSpace: 'pre-wrap'}}>
                                <div dangerouslySetInnerHTML={{__html: html}}></div>
                            </p>
                        )
                }
            </div>
        </>
    );
};

export default StreamComponent;
