import {Request, Response} from "express";
// @ts-ignore
import fs from "fs";
import {getSession} from "next-auth/react";
import clientPromise from "../../lib/mongodb";
import {ObjectId} from "mongodb";


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
    // @ts-ignore
    const images = await db.collection("images").find({userId: ObjectId(userId)}).toArray();
    console.log(images);
    res.json(images);
}
