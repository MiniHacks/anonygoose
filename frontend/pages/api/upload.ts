import { Request, Response } from "express";
import { File } from "formidable";
import Formidable from "formidable-serverless";
// @ts-ignore
import fs from "fs";
import {getSession} from "next-auth/react";
import { uuid } from 'uuidv4';
import clientPromise from "../../lib/mongodb";
import {ObjectId} from "mongodb";
import path from "path";


export const config = {
    api: {
        bodyParser: false,
    },
};

export default async function uploadFormFiles(
    req: Request,
    res: Response
) {
    const mongoClient = await clientPromise;
    const db = mongoClient.db();
    const session = await getSession({req})
    const userId = session.user["_id"];
    const imageId = uuid();
    return new Promise(async (resolve, reject) => {
        const form = new Formidable.IncomingForm({
            multiples: true,
            keepExtensions: true,
        });

        form
            .on("file", async (name: string, file: File) => {
                const data = fs.readFileSync(file.path);
                const ending = file.name.split(".").reverse()[0];
                const imagesFolder = process.env.IMAGE_PATH || "/app"
                const filepath = `${imagesFolder}/images/${imageId}.${ending}`
                console.log(filepath);
                fs.writeFileSync(filepath, data);
                fs.unlinkSync(file.path);
                await db.collection("images").insertOne({
                    path: filepath.substring(6),
                    // @ts-ignore
                    userId: ObjectId(userId)
                });
                resolve(res.json({filepath}))
            })
            .on("aborted", () => {
                reject(res.status(500).send('Aborted'))
            })
            .on("end", () => {
                // resolve(res.status(200).json('done'));
            });

        await form.parse(req)
    });
}
